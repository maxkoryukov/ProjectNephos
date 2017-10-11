# -*- coding: utf-8 -*-

import logging
from flask import Blueprint
# from flask import json

from flask_restful import Resource
from flask_restful import Api
from flask_restful import reqparse
from flask_restful import marshal_with
from flask_restful import fields

import arrow

from ._utils import marshal_nullable_with

from ..models.jobs import JobInfo

log = logging.getLogger(__name__)

api_blueprint = Blueprint('api', __name__)
api = Api(api_blueprint)


# output
job_fields = {
	'ID': fields.String,
	'name': fields.String,
	'date_from': fields.DateTime(dt_format='iso8601'),
	'date_trim': fields.DateTime(dt_format='iso8601'),
}


def to_datetime(string):
	if string is None:
		return string
	d = arrow.get(string)
	return d.datetime


def as_is(arg):
	return arg


class JobsListResource(Resource):

	# input
	parser = reqparse.RequestParser()
	parser.add_argument('name')
	parser.add_argument('date_from', type=to_datetime)
	parser.add_argument('date_trim', type=to_datetime)
	parser.add_argument('job_params', type=as_is)
	parser.add_argument('template_name')

	@marshal_with(job_fields, envelope='data')
	def get(self):
		jjs = JobInfo.query.all()

		return jjs

	# CREATE JOB
	@marshal_with(job_fields, envelope='data')
	def post(self):
		args = self.parser.parse_args()
		log.debug('job create, args: %s', args)

		jj = JobInfo()
		jj.name = args.name
		jj.date_from = arrow.now().shift(seconds=3).datetime  #   args.date_from
		jj.date_trim = args.date_trim
		jj.template_name = args.template_name
		jj.job_params = args.job_params

		jj.save()

		return jj


api.add_resource(JobsListResource, '/jobs')


class JobsResource(Resource):

	@marshal_nullable_with(job_fields, envelope='data')
	def get(self, ID):
		jj = JobInfo.query.filter_by(ID=ID).first()

		return jj


api.add_resource(JobsResource, '/jobs/<string:ID>')
